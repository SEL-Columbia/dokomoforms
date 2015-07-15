var React = require('react');

module.exports = React.createClass({
    render: function() {
        return (
                <div className="input_container">
                    <input 
                        type={this.props.type ? this.props.type : "text"} 
                        placeholder="Please provide a response." 
                        value=""
                     >
                     {this.props.showMinus ? 
                        <span className="icon icon-close question__minus"></span>
                        : null}
                    </input>
                 </div>
               )
    }
});
