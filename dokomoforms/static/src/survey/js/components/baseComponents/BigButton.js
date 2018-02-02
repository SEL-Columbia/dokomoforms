var React = require('react'),
    createReactClass = require('create-react-class');

/*
 * Big 'ol button
 *
 * props:
 *  @type: Type of button (class name from ratchet usually) defaults to btn-primary
 *  @buttonFunction: What to do on click events
 *  @text: Text of the button
 */
module.exports = createReactClass({
    render: function() {
        var buttonClasses = 'btn btn-block navigate-right page_nav__next';
        if (this.props.type) {
            buttonClasses += ' ' + this.props.type;
        } else {
            buttonClasses += ' btn-primary';
        }

        return (
            <div className='bar-padded'>
                <button onClick={this.props.buttonFunction} className={buttonClasses}>
                    {this.props.text}
                </button>
            </div>
       );
    }
});
