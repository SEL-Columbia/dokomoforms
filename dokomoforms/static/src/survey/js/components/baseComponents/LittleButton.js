var React = require('react'),
    createReactClass = require('create-react-class');

/*
 * Little weeny button
 *
 * props:
 *  @type: Type of button (class name from ratchet usually) defaults to btn-primary
 *  @buttonFunction: What to do on click events
 *  @text: Text of the button
 *  @icon: Icon if any to show before button text
 *  @disabled: Whether or not the button should be disabled
 */
module.exports = createReactClass({
    render: function() {
        var iconClass = 'icon icon-inline-left ' + this.props.icon;
        var classes = 'btn ';
        classes += this.props.extraClasses || '';
        return (
            <div className='content-padded'>
                <button className={classes}
                    disabled={this.props.disabled}
                    onClick={this.props.buttonFunction} >

                    {this.props.icon ? <span className={iconClass}></span> : null }
                    {this.props.text}
                </button>
            </div>
       );
    }
});
