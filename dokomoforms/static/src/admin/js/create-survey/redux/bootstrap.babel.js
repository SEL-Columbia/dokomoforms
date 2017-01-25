export default function bootstrap(orm) {
    
    // Get the empty state according to our schema.
    const state = orm.getEmptyState();

    // Begin a mutating session with that state.
    // `state` will be mutated.
    const session = orm.mutableSession(state);

    // Model classes are available as properties of the
    // Session instance.
    const { Survey, Node } = session;

    // Start by creating entities whose props are not dependent
    // on others

    // const middle = Node.create({id: 89, node: {}})

    // const last = Survey.create({
    //     id: 1010,
    //     default_language: 'English',
    //     nodes: [middle]
    // })

    // const first = Node.create({id: 6, node: {}, sub_surveys: [last]})

    const another = Survey.create({
        id: 1004,
        default_language: 'English',
        node: 1,
        buckets: [{bucket: 'bucket'}]
    })

    const survey = Survey.create({
        id: 1001,
        default_language: 'English'
    });

    const node = Node.create({id: 1, node: {}, survey: 1001})

    console.log('newest survey', survey, state)
    
    // Return the whole Redux initial state.
    return {
        orm: state,
        currentSurveyId: 1001
    };
}
