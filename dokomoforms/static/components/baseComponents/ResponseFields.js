var React = require('react');
var ResponseField = require('./ResponseField.js');

module.exports = React.createClass({
    render: function() {
        var children = Array.apply(null, {length: this.props.childCount})
        return (
                <div>
                {children.map(function(child, idx) {
                    return <ResponseField key={idx + 1} showMinus={true}/>;
                })}
                </div>
               )
    }
});

