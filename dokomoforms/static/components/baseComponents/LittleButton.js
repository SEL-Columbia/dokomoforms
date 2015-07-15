var React = require('react');
module.exports = React.createClass({
    render: function() {
        var iconClass = "icon " + this.props.icon;
        return (
                <div className="content-padded">
                    <button className="btn">
                        {this.props.icon ? <span className={iconClass}></span> : null }
                        {this.props.text}
                    </button>
                </div>
               )
    }
});

