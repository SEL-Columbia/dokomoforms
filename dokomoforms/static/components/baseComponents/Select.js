var React = require('react'); 
ResponseField = require('./ResponseField.js');

/*
 * Select component
 * Handles drop down and other input rendering
 *
 * props:
 *  @multiSelect: Boolean to activate multiselect mode
 *  @choices: Array of choices in Select, expects a dict with value and text
 *  @withOther: Allow for other responses, adds it to the choices and renders 
 *      a ResponseField when selected
 */
module.exports = React.createClass({
    getInitialState: function() {
        return { showOther: false }
    },

    onChange: function(e) {
        var foundOther = false;
        for (var i = 0; i < e.target.selectedOptions.length; i++) {
            option = e.target.selectedOptions[i]; 
            foundOther = foundOther | option.value === "other";
        }

        this.setState({showOther: foundOther})
    },

    render: function() {
       var size = this.props.multiSelect ? 
           this.props.choices.length + 1 + 1*this.props.withOther : 1;
        return (
                <div className="content-padded">
                    <select className="noselect" onChange={this.onChange} 
                            multiple={this.props.multiSelect}
                            size={size}
                    >

                    <option key="null" value="null">Please choose an option</option>
                    {this.props.choices.map(function(choice) {
                        return (
                                <option key={choice.value} value={choice.value}>
                                    { choice.text }
                                </option>
                                )
                    })}
                    {this.props.withOther ? 
                        <option key="other" value="other"> Other </option> 
                        : null}
                    </select>
                    {this.state.showOther ? <ResponseField />: null}
                </div>
               )

    }
});

