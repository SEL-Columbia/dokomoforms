var React = require('react'),
    createReactClass = require('create-react-class');

/*
 * Card component
 *
 * props:
 *  @type: Card type (class name from ratchet usually) defaults to message-primary
 *  @msg: Array of messages, each element is placed on a new line. JSX accepted
 */
module.exports = createReactClass({
    render: function() {
        var messageClass = 'message-box';
        if (this.props.type) {
            messageClass += ' ' + this.props.type;
        } else {
            messageClass += ' message-primary';
        }

        return (
            <div className='content-padded'>
                <div className={messageClass} >
                {this.props.messages.map(function(msg, idx) {
                    return (
                            <span key={idx}> {msg} <br/> </span>
                        );
                })}
                </div>
            </div>
       );
    }
});
