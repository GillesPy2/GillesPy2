import ast
try:
    import libsbml
except ImportError:
    raise ImportError('libsbml is required to convert GillesPy models to SBML files.')


def __get_math(math):
    replacements = {
            "log": "ln",
            "**": "^",
            "and": "&&",
            "or": "||"
            }
    for old, new in replacements.items():
        math_str = math.replace(old, new)
    return libsbml.parseL3Formula(math_str)

def __add_species(species_list, model):
    for name, species in species_list.items():
        spec = model.createSpecies()
        spec.initDefaults()
        spec.setCompartment("c")
        spec.setId(name)
        spec.setInitialAmount(species.initial_value)

def __add_parameters(parameter_list, model):
    for name, parameter in parameter_list.items():
        param = model.createParameter()
        param.initDefaults()
        param.setId(name)
        try:
            param.setValue(ast.literal_eval(parameter.expression))
        except ValueError:
            param.setValue(parameter.expression)

def __add_reactions(reaction_list, model):
    for name, reaction in reaction_list.items():
        reac = model.createReaction()
        reac.initDefaults()
        reac.setId(name)

        __add_reactants(reaction.reactants, reac)
        __add_products(reaction.products, reac)

        propensity = __get_math(reaction.propensity_function)
        kin_law = reac.createKineticLaw()
        kin_law.setMath(propensity)

def __add_reactants(reactant_list, reaction):
    for spec, ratio in reactant_list.items():
        react = reaction.createReactant()
        react.setConstant(True)
        react.setSpecies(spec.name)
        react.setStoichiometry(ratio)

def __add_products(product_list, reaction):
    for spec, ratio in product_list.items():
        prod = reaction.createProduct()
        prod.setConstant(True)
        prod.setSpecies(spec.name)
        prod.setStoichiometry(ratio)

def __add_events(event_list, model):
    for name, event in event_list.items():
        evt = model.createEvent()
        evt.setId(name)
        evt.setUseValuesFromTriggerTime(event.use_values_from_trigger_time)
        
        if event.delay is not None:
            delay = __get_math(event.delay)
            dly = evt.createDelay()
            dly.setMath(delay)

        priority = __get_math(event.priority)
        prior = evt.createPriority()
        prior.setMath(priority)

        trigger = event.trigger
        expression = __get_math(trigger.expression)
        trig = evt.createTrigger()
        trig.setInitialValue(trigger.value)
        trig.setPersistent(trigger.persistent)
        trig.setMath(expression)

        __add_event_assignments(event.assignments, evt)

def __add_event_assignments(assignment_list, event):
    for assignment in assignment_list:
        assign = event.createEventAssignment()
        assign.setVariable(assignment.variable.name)

        exxpression = __get_math(assignment.expression)
        assign.setMath(expression)

def __add_rate_rules(rate_rule_list, model):
    for name, rule in rate_rule_list.items():
        r_rule = model.createRateRule()
        r_rule.setId(name)
        r_rule.setVariable(rule.variable)
        formula = __get_math(rule.formula)
        r_rule.setMath(formula)

def __add_assignment_rules(assignment_rule_list, model):
    for name, rule in assignment_rule_list.items():
        a_rule = model.createAssignmentRule()
        a_rule.setId(name)
        a_rule.setVariable(rule.variable)
        formula = __get_math(rule.formula)
        a_rule.setMath(formula)

def __add_function_definitions(function_definition_list, model):
    for name, function_def in function_definition_list.items():
        func_def = model.createFunctionDefinition()
        func_def.setId(name)
        function = __get_math(function_def.function_string)
        func_def.setMath(function)

def __write_to_file(document, path):
    writer = libsbml.SBMLWriter()

    with open(path, "w") as sbml_file:
        sbml_file.write(writer.writeSBMLToString(document))

def export(model, path=None):

    if path is None:
        path = f"{model.name}.xml"

    document = libsbml.SBMLDocument(3, 2)

    sbml_model = document.createModel()
    sbml_model.setName(model.name)

    compartment = sbml_model.createCompartment()
    compartment.setId('c')
    compartment.setConstant(True)
    compartment.setSize(1)
    compartment.setSpatialDimensions(3)

    __add_species(model.listOfSpecies, sbml_model)
    __add_parameters(model.listOfParameters, sbml_model)
    __add_reactions(model.listOfReactions, sbml_model)
    __add_events(model.listOfEvents, sbml_model)
    __add_rate_rules(model.listOfRateRules, sbml_model)
    __add_assignment_rules(model.listOfAssignmentRules, sbml_model)
    __add_function_definitions(model.listOfFunctionDefinitions, sbml_model)

    __write_to_file(document, path)

    return path
