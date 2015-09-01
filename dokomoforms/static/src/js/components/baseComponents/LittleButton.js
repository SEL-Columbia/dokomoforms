var React = require('react');

/*
 * Little weeny button
 *
 * props:
 *  @type: Type of button (class name from ratchet usually) defaults to btn-primary
 *  @buttonFunction: What to do on click events
 *  @text: Text of the button
 *  @icon: Icon if any to show before button text
 */
module.exports = React.createClass({
    render: function() {
        var iconClass = 'icon ' + this.props.icon;
        return (
                <div className="content-padded">
                    <button className="btn"
                        disabled={this.props.disabled}
                        onClick={this.props.buttonFunction} >

                        {this.props.icon ? <span className={iconClass}></span> : null }
                        {this.props.text}
                    </button>
                </div>
               );
    }
});

