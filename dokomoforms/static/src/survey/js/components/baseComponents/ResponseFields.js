var React = require('react'),
    createReactClass = require('create-react-class'),
    ResponseField = require('./ResponseField.js');

/*
 * Array of ResponseField
 *
 * Refer to ResponseField for use
 * XXX Remove Component
 */
module.exports = createReactClass({
    render: function() {
        var children = Array.apply(null, {length: this.props.childCount});
        var self = this;
        return (
                <div>
                {children.map(function(child, idx) {
                    return (
                            <ResponseField
                                buttonFunction={self.props.buttonFunction}
                                onInput={self.props.onInput}
                                type={self.props.type}
                                key={idx + 1}
                                index={idx}
                                showMinus={self.props.childCount > 1}
                            />
                           );
                })}
                </div>
               );
    }
});
