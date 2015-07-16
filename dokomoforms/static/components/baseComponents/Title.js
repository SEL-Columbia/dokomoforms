var React = require('react');
module.exports = React.createClass({
    render: function() {
        return ( 
                <div className="content-padded">
                    <h3>{this.props.title}</h3>
                    <p>{this.props.message}</p>
                </div>
               )
    }
});
