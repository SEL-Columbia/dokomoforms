var React = require('react'),
    createReactClass = require('create-react-class');

var ResponseField = require('./baseComponents/ResponseField.js');
var ResponseFields = require('./baseComponents/ResponseFields.js');
var BigButton = require('./baseComponents/BigButton.js');
var LittleButton = require('./baseComponents/LittleButton.js');

var Title = require('./baseComponents/Title.js');
var Card = require('./baseComponents/Card.js');
var Select = require('./baseComponents/Select.js');
var FacilityRadios = require('./baseComponents/FacilityRadios.js');
var Message = require('./baseComponents/Message.js');

var Header = require('./baseComponents/Header.js');
var Footer = require('./baseComponents/Footer.js');

var Application = createReactClass({
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

React.render(
        <Application />,
        document.body
);
