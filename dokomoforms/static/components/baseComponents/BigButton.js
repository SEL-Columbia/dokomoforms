var React = require('react');
module.exports = React.createClass({
    render: function() {
        var buttonClasses = "btn btn-block navigate-right page_nav__next";
        if (this.props.type) {
            buttonClasses += " " + this.props.type;
        } else {
            buttonClasses += " btn-primary";
        }

        return (
                <div className="bar-padded">
                    <button onClick={this.props.buttonFunction} className={buttonClasses}>
                        {this.props.text}
                    </button>
                </div>
               )
    }
});

