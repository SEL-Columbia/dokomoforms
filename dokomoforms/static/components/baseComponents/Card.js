var React = require('react'); 
module.exports = React.createClass({
    render: function() {
        var messageClass = "message-box";
        if (this.props.type) { 
            messageClass += " " + this.props.type;
        } else {
            messageClass += " message-primary";
        }

        var self = this;
        return (
            <div className="content-padded">
                <div className={messageClass} >
                {this.props.messages.map(function(msg, idx) {
                    return ( 
                            <span> {msg} <br/> </span> 
                        )
                })}
                </div>
            </div>
       )
    }
});
