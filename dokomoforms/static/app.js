var React = require('react');

var ResponseField = React.createClass({
    render: function() {
        return (
                <input type="text" placeholder="Your name here" />
               )
    }
});

var ResponseFields = React.createClass({
    render: function() {
        var children = Array.apply(null, {length: this.props.childCount})
        return (
                <div>
                {children.map(function(child, idx) {
                    return <ResponseField key={idx + 1} />;
                })}
                </div>
               )
    }
});

var Title = React.createClass({
    render: function() {
        return ( 
                <div className="content-padded">
                    <h3>test_survey</h3>
                    <p>version 1 | last updated Thu Jul 02 2015</p>
                </div>
               )
    }
});

var BigButton = React.createClass({
    render: function() {
        return (
                <div className="bar-padded">
                <button className="btn btn-block btn-primary navigate-right page_nav__next">
                {this.props.text}
                </button>
                </div>
               )
    }
});

var Footer = React.createClass({
    render: function() {
        return (
                <div className="bar bar-standard bar-footer bar-footer-extended">
                    <BigButton text={'Next Question'} />
                    <div className="question__btn__other">
                        <input type="checkbox" id="dont-know" name="dont-know" value="selected" />
                        <label for="dont-know">I don't know the answer</label>
                    </div>
                </div>
               )
    }
});

var Question = React.createClass({
    render: function() {
        return (
                <div className="content">
                    <Title />
                    <ResponseFields childCount={3} />
                </div>
               )
    }
});

var Menu = React.createClass({
    render: function() {
        return (
            <div className="title_menu">
                <div className="title_menu_option menu_restart">
                    Cancel survey
                </div>
                <div className="title_menu_option menu_save">
                    Save current state and exit
                </div>
                <div className="title_menu_option menu_clear">
                    Clear all saved surveys
                </div>
            </div>
       )
    }
});

var Header = React.createClass({
    getInitialState: function() {
        return { showMenu: false }
    },
    onClick: function() {
        this.setState({showMenu: this.state.showMenu ? false : true })
    },
    render: function() {
        return (
            <header className="bar bar-nav bar-padded">
            <h1 className="title align-left">independant</h1>
            <a className="icon icon-bars pull-right menu"
                onClick = {this.onClick}
            ></a>
            { this.state.showMenu ? <Menu /> : null }
            </header>
        )
    }

});

var Application = React.createClass({
    render: function() {
        return (
                <div id="wrapper">
                    <Header />
                    <Question />
                    <Footer />
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
