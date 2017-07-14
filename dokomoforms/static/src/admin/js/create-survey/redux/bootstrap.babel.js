'use strict';

export default function bootstrap(orm) {
    
    // Get the empty state according to our schema.
    const state = orm.getEmptyState();

    // Begin a mutating session with that state.
    // `state` will be mutated.
    const session = orm.mutableSession(state);

    // Model classes are available as properties of the
    // Session instance.
    const { Survey, Node, Question, Bucket } = session;

    const survey = Survey.create({
        id: 1001,
        default_language: 'English',
        survey_type: 'public'
    });

    const node = Node.create({id: 1, survey: 1001});

    const question = Question.create({
        title: {'English': 'How far away (in kilometers) is your home from a hospital?'},
        id: 1,
        node: 1,
    });

    const survey2 = Survey.create({
        node: 1,
        id: 1002,
    });

    const node2 = Node.create({id: 2, survey: 1002});

    const question2 = Question.create({
        id: 2,
        node: 2
    })

    const bucket1 = Bucket.create({
        survey: 1002,
        bucket_type: 'integer',
        bucket: '[0, 5]'
    })

    console.log('newest survey', survey, node, question, state)
    
    // Return the whole Redux initial state.
    return {
        orm: state,
        currentSurveyId: 1001,
        default_language: 'English'
    };
}
