#include "tau.h"
#include <vector>
#include <iostream>
#include <memory>
#include <string>
#include <cmath>        // std::abs
#include <algorithm>
TauArgs initialize(Gillespy::Model &model, double tau_tol){

   // Initialize TauArgs struct to be returned as a pointer
   TauArgs tau_args;
   // Initialize highest order rxns to 0
   for (int i=0; i<model.number_species; i++){
       tau_args.HOR[model.species[i].name] = 0;
   }
   // initize mu_i, sigma_i


   // Create list of reactions
   for (int r=0; r<model.number_reactions; r++){
       //Calculate reaction r's rxn order
       int rxn_order = 0;
       for (int s=0; s<model.number_species; s++){
           if (model.reactions[r].species_change[s]<0)
               rxn_order += 1;
       }

       for (int reactant=0; reactant<model.number_species; reactant++){
           if (model.reactions[r].species_change[reactant]<0){ // << the absolute value for this line is "count" in tau.py
               //insert reactant into set, ordered by species id (found in Gillespy::Species struct)
               tau_args.reactants.insert(model.species[reactant]);              

               // if this reaction's order is higher than previous, set
               if (rxn_order > tau_args.HOR[model.species[reactant].name]){
                   tau_args.HOR[model.species[reactant].name] = rxn_order;
                   tau_args.g_i[model.species[reactant].name] = tau_args.HOR[model.species[reactant].name];

                   int count = std::abs(model.reactions[r].species_change[reactant]);
                   if (count == 2 && rxn_order == 2){
                       auto lambda = [](double x) {return (2 + (1 / (x - 1)));};
                       tau_args.g_i_lambdas[model.species[reactant].name] = lambda;
                   }
                   else if(count == 2 && rxn_order == 3){
                       auto lambda = [](double x) {return ((3 / 2) * (2 + (1 / (x - 1))));};
                       tau_args.g_i_lambdas[model.species[reactant].name] = lambda;
                   }
                   else if (count == 3){
                       auto lambda = [](double x) {return (3 + (1 / (x - 1)) + (2 / (x - 2)));};
                       tau_args.g_i_lambdas[model.species[reactant].name] = lambda;
                   }
                   else{
                       tau_args.g_i[model.species[reactant].name] = tau_args.HOR[model.species[reactant].name];
                       tau_args.epsilon_i[model.species[reactant].name] = tau_tol / tau_args.g_i[model.species[reactant].name];
                   }


               }
           }
       }

   //END OF LIST OF RXNS
   }
   return tau_args;
}

double select(Gillespy::Model &model, TauArgs tau_args, const double tau_tol, const double current_time, const int save_time, double *propensity_values, int *current_state){
    double tau; //tau time to step;
    std::map<std::string,double> critical_taus;    //Mapping of possible critical_taus, to be evaluated
    std::map<std::string,double> mu_i;
    std::map<std::string,double> sigma_i;
    bool critical = false;  // system-wide flag, true when any reaction is critical
    double non_critical_tau = 0;  // holds the smallest tau time for non-critical reactions
    double critical_tau = 0;  // holds the smallest tau time for critical reactions

    //DEBUG FOR ME TO DELETE L8R!!
    bool debug = false;
    int v;//used for number of population reactant consumes

    // initialize mu_i and sigma_i to 0
    for(int spec = 0; spec<model.number_species; spec++){
            mu_i[model.species[spec].name]= 0;
            sigma_i[model.species[spec].name] = 0;

        }
    // Determine if there are any critical reactions
    for (int reaction = 0; reaction < model.number_reactions; reaction++){
        for (int reactant = 0; reactant < model.number_species; reactant++){
            if (model.reactions[reaction].species_change[reactant]<0){
                v = abs(model.reactions[reaction].species_change[reactant]);
                if ((double)current_state[reactant] / v < tau_args.critical_threshold && propensity_values[reaction] > 0)
                    critical = true;
            }
        }
    }

    // If a critical reaction is present, estimate tau for a single firing of each
    // critical reaction with propensity > 0, and take the smallest tau
    if (critical == true){
        for (int reaction = 0; reaction < model.number_reactions; reaction++){
            if (propensity_values[reaction]>0)
                critical_taus[model.reactions[reaction].name] = 1/propensity_values[reaction];
        }

        // Find min of critical tau if present
        if (critical_taus.size()>0){
            std::pair<std::string, double> min;
            //find min of tau_i
            min = *min_element(critical_taus.begin(), critical_taus.end(),[](const auto& lhs, const auto& rhs){ return lhs.second < rhs.second;});
            critical_tau = min.second;
        }
    }

    if (tau_args.g_i_lambdas.size()>0){
        for (auto const& x : tau_args.g_i_lambdas)
           {
               tau_args.g_i[x.first] = tau_args.g_i_lambdas[x.first](tau_args.g_i[x.first]);
               tau_args.epsilon_i[x.first] = tau_tol / tau_args.g_i[x.first];
               tau_args.g_i_lambdas.erase(x.first);//MAYBE SHOULDN'T ERASE, may break loop/may be understanding this part wrong
           }
    }

    std::map<std::string,double> tau_i;    //Mapping of possible critical_taus, to be evaluated


    for (int reaction = 0; reaction < model.number_reactions; reaction++){
        for (int reactant = 0; reactant < model.number_species; reactant++){
            if (model.reactions[reaction].species_change[reactant]<0){
                int consumed = abs(model.reactions[reaction].species_change[reactant]);
                mu_i[model.species[reactant].name] += consumed*propensity_values[reaction];//Cao, Gillespie, Petzold 32a
                sigma_i[model.species[reactant].name] += std::pow(consumed,2) * propensity_values[reaction];//Cao, Gillespie, Petzold 32a
           }
        }
    }

    for (const auto &r : tau_args.reactants)
    {
        double calculated_max = tau_args.epsilon_i[r.name] * current_state[r.id];
        double max_pop_change_mean;
        if (calculated_max < 1)
                max_pop_change_mean = 1;
        else
            max_pop_change_mean = calculated_max;

        double max_pop_change_sd = pow(max_pop_change_mean,2);

        if (mu_i[r.name] > 0){ // Cao, Gillespie, Petzold 33
            tau_i[r.name] = std::min(std::abs(max_pop_change_mean / mu_i[r.name]),max_pop_change_sd / sigma_i[r.name]);
        }
    }

    if (tau_i.size()>0){
        std::pair<std::string, double> min;
        //find min of tau_i
        min = *min_element(tau_i.begin(), tau_i.end(),[](const auto& lhs, const auto& rhs){ return lhs.second < rhs.second;});
        non_critical_tau = min.second;
    }


    // If all reactions are non-critical, use non-critical tau.
    if (critical == false)
        tau = non_critical_tau;

    // If all reactions are critical, use critical tau.
    else if (tau_i.size()==0)
        tau = critical_tau;
    // If there are both critical, and non critical reactions,
    // Take the shortest tau between critica and non-critical.
    else
        tau = std::min(non_critical_tau, critical_tau);
    // If selected tau exceeds save time, integrate to save time
    if (tau > 0)
        tau = std::max(tau, 1e-10);
        if (save_time - current_time > 0)
            tau = std::min(tau, save_time - current_time);
    else{
        tau = save_time - current_time;
    }

    return tau;
}
