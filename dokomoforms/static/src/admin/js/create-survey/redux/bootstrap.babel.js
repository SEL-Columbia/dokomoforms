export default function bootstrap(orm) {
    
    // Get the empty state according to our schema.
    const state = orm.getEmptyState();

    // Begin a mutating session with that state.
    // `state` will be mutated.
    const session = orm.mutableSession(state);

    // Model classes are available as properties of the
    // Session instance.
    const { Survey, Node, Question } = session;

    const survey = Survey.create({
        id: 1001,
        default_language: 'English'
    });

    const node = Node.create({id: 1, survey: 1001})

    const question = Question.create({
        id: 1,
        node: 1
    })

    console.log('newest survey', survey, node, question, state)
    
    // Return the whole Redux initial state.
    return {
        orm: state,
        currentSurveyId: 1001
    };
}
