var React = require('react'); 
var BigButton = require('./BigButton.js');
var DontKnow = require('./DontKnow.js');

module.exports = React.createClass({
    render: function() {
        var FooterClasses = "bar bar-standard bar-footer";
        if (this.props.showDontKnow) 
            FooterClasses += " bar-footer-extended";
        return (
                <div className={FooterClasses}>
                    <BigButton text={'Next Question'} />
                    { this.props.showDontKnow ? <DontKnow /> : null }
                </div>
               )
    }
});

