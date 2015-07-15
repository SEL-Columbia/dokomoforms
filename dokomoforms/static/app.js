var React = require('react');
var ResponseField = require('./components/baseComponents/ResponseField.js');
var Header = require('./components/baseComponents/Header.js');
var Title = require('./components/baseComponents/Title.js');
var Card = require('./components/baseComponents/Card.js');
var BigButton = require('./components/baseComponents/BigButton.js');
var LittleButton = require('./components/baseComponents/LittleButton.js');
var ResponseFields = require('./components/baseComponents/ResponseFields.js');
var Select = require('./components/baseComponents/Select.js');
var FacilityRadios = require('./components/baseComponents/FacilityRadios.js');
var Footer = require('./components/baseComponents/Footer.js');
var Message = require('./components/baseComponents/Message.js');

var Application = React.createClass({
    getInitialState: function() {
        return { showDontKnow: true }
    },
    render: function() {
        var contentClasses = "content";
        if (this.state.showDontKnow) 
            contentClasses += " content-shrunk";

        return (
                <div id="wrapper">
                    <Header splash={true}/>
                    <div className={contentClasses}>
                        <Title />
                        <Card messages={["hey", "how you doing", 
                            ["i ", <b>love</b>, " toast"]]} type={"message-error"}/>
                        <Card messages={["cool"]} />
                        <BigButton text={'Click for toast'} type={'btn-positive'} />
                        <ResponseFields childCount={3}/>
                        <LittleButton text={'add another answer'} />
                        <Select withOther={true} multiSelect={true} choices={[
                            {'value': 'toast', 'text': 'i love toast'},
                            {'value': 'hater', 'text': 'i hate toast'}
                        ]}/>
                        <ResponseField showMinus={false}/>
                        <FacilityRadios facilities={[
                            {'name': 'toast factory', 'distance': 100, 'sector': 'toastustry', 'value': 123456},
                            {'name': 'toast store', 'distance': 200, 'sector': 'toastomerce', 'value': 77896},
                            {'name': 'toast park', 'distance': 1000, 'sector': 'toastheme', 'value': 78906},
                            {'name': 'toast app', 'distance': 50, 'sector': 'Etoast', 'value': 011126}
                        ]}/>
                        <Select choices={[
                            {'value': 'toast', 'text': 'i love toast'},
                            {'value': 'hater', 'text': 'i hate toast'}
                        ]}/>
                        <LittleButton icon={"icon-star"} text={' find me'} />
                        <Message text={"toast? toast! TOOOOASSTTT!!!"}/>
                    </div>
                    <Footer showDontKnow={this.state.showDontKnow}/>
                </div>
               )
    }
});

var ApplicationData = {};
init = function(survey) {
    ApplicationData.survey = survey;
    React.render(
            <Application />,
            document.body
    );
};
