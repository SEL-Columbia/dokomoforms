'use strict';

import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { pathSelector } from './../redux/selectors.babel.js';


class SideBar extends React.Component {

    constructor(props) {

        super(props);

        this.listQuestions = this.listQuestions.bind(this);

        this.state = {};
    }

    listQuestions() {

        const testpath = [
        ]

        return testpath.map(function(question) {
            return(
                <li>
                    <p className="question">{question.title.English}</p>
                    {(question.buckets && question.buckets.length<1) &&
                        <p className="arrow glyphicon glyphicon-triangle-bottom"></p>
                    }
                </li>
            )
        })
    }

    render() {
        console.log('sideprops', this.props)
        return (
            <div id="sidebar">
                <ul>
                    {this.listQuestions()}
                </ul>
                <div id="sidebar-bottom">
                    {(this.props.surveyId!==1001) &&
                        <button id="back-button">back</button>
                    }
                    {(this.props.surveyId===1001) &&
                        <button id="submit">submit</button>
                    }
                </div>
            </div>
        )
    }

}

function mapStateToProps(state){
    console.log('map state sidebar', state);
    return {
        questionPath: pathSelector(state)
    };
}

// function matchDispatchToProps(dispatch){
//     return bindActionCreators({updateCurrentSurvey: updateCurrentSurvey,
//                                 updateSurvey: updateSurvey}, dispatch);
// }

export default connect(mapStateToProps)(SideBar);
