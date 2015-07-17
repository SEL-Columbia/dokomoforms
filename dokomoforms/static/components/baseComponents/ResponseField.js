var React = require('react');

module.exports = React.createClass({
    getResponseType: function() {
        var type = this.props.type;
        console.log(type);
        switch(type) {
            case "integer":
            case "decimal":
            case "location":
                return "number"
            case "timestamp":
            case "time":
                return "time"
            case "date":
                return "date"
            default:
                return "text"
        }
    }, 
    render: function() {
        return (
                <div className="input_container">
                    <input 
                        type={this.getResponseType()} 
                        placeholder="Please provide a response." 
                     >
                     {this.props.showMinus ? 
                        <span 
                            onClick={this.props.buttonFunction} 
                            className="icon icon-close question__minus">
                        </span>
                        : null}
                    </input>
                 </div>
               )
    }
});
