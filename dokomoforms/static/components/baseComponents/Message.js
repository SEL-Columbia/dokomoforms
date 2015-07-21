var React = require('react');

/*
 * Message component
 *
 * @text: text to render
 */
module.exports = React.createClass({
    render: function() {
        var textClass = this.props.classes;
        return (
                <div className='content-padded'>
                        <p className={textClass}>{this.props.text}</p>
                </div>
               )
    }
});

