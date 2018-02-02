var React = require('react'),
    createReactClass = require('create-react-class');

/*
 * Message component
 *
 * @text: text to render
 */
module.exports = createReactClass({
    render: function() {
        var textClass = this.props.classes;
        return (
            <div className='content-padded'>
                <p className={textClass}>{this.props.text}</p>
            </div>
        );
    }
});
