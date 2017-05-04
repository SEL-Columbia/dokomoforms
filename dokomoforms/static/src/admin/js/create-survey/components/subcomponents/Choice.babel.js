'use strict';

import utils from './../../utils.js';


export default function Choice(props) {

    function choiceHandler(event) {
        if (event.target.value.length < 1) return;
        const choice_text = {};
        choice_text[props.default_language] = event.target.value;
        const choice = Object.assign({}, {choice_text: choice_text});
        if (props.choiceId===0) {
            choice.id = utils.addId('choice');
            choice.question = props.questionId;
            props.addChoice(choice);
        } else {
            choice.id = props.choiceId;
            props.updateChoice(choice);
        }
    }

    return(
        <div className='choice'>
            <div className='choice-text-area'>
                <label>{props.index}.</label>
                <textarea className="choice-text" rows="1"
                    defaultValue={props.answer} onBlur={choiceHandler}
                    readOnly={props.answer==="other"}/>
            </div>
            {(props.deleteChoice) &&
                <button
                 disabled={props.choiceId===0}
                 onClick={props.deleteChoice.bind(null, props.choiceId)}>X</button>
            }
        </div>
    );
}