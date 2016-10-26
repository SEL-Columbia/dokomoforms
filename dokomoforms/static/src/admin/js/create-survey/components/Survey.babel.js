import React from 'react';

class Survey extends React.Component {

    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);

        this.state = {
            title: ''
        };
    }

    updateTitle(event) {
        this.setState({title: event.target.value})
    }

    render() {
        return (
            <div>
                <SurveyInfo data={this.state.title} updateStateProp={this.updateTitle}>
                {this.state.title}</SurveyInfo>
            </div>
        );
    };
};

class SurveyInfo extends React.Component {

    render() {
      return (
         <div>
            <input type="text" value={this.props.data} 
               onChange={this.props.updateStateProp} />
            <h3>{this.props.data}</h3>
         </div>
      );
   }

}

export default Survey;