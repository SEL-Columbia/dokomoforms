var React = require('react'),
    createReactClass = require('create-react-class'),
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
 *  @onInput: What to do on valid other input
 *  @onSelect: What to do on selection
 */
module.exports = createReactClass({
    getInitialState: function() {
        return {
            showOther: this.props.initSelect && this.props.initSelect.indexOf('other') > -1
        };
    },

    onChange: function(e) {
        var foundOther = false;
        var options = [];
        for (var i = 0; i < e.target.selectedOptions.length; i++) {
            var option = e.target.selectedOptions[i];
            foundOther = foundOther | option.value === 'other';
            options[i] = option.value;
        }

        if (this.props.onSelect)
            this.props.onSelect(options);

        this.setState({
            showOther: foundOther
        });
    },

    render: function() {
        var size = this.props.multiSelect ?
            this.props.choices.length + 1 + 1 * this.props.withOther : 1;
        return (
            <div className="content-padded">
                    <select className="noselect" onChange={this.onChange}
                            multiple={this.props.multiSelect}
                            size={size}
                            defaultValue={this.props.multiSelect
                                ? this.props.initSelect
                                : this.props.initSelect
                                    ? this.props.initSelect[0]
                                    : null
                            }
                            disabled={this.props.disabled}
                    >

                    <option key="null" value="null">
                        {this.props.placeholder || 'Please choose an option...'}
                    </option>
                    {this.props.choices.map(function(choice) {
                        return (
                                <option key={choice.value} value={choice.value}>
                                    { choice.text }
                                </option>
                            );
                    })}
                    {this.props.withOther ?
                        <option key="other" value="other"> Other </option>
                        : null}
                    </select>
                    {this.state.showOther
                        ?   <ResponseField
                                disabled={this.props.disabled}
                                onInput={this.props.onInput}
                                initValue={this.props.initValue}
                            />
                        :   null
                    }
                </div>
        );

    }
});
