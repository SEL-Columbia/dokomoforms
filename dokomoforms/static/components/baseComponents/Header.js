var React = require('react');
var Menu = require('./Menu.js');

module.exports = React.createClass({
    getInitialState: function() {
        return { showMenu: false }
    },

    onClick: function() {
        this.setState({showMenu: this.state.showMenu ? false : true })
    },

    render: function() {
        var headerClasses = "bar bar-nav bar-padded noselect";
        if (this.state.showMenu) 
            headerClasses += " title-extended";

        return (
            <header className={headerClasses}>
            {this.props.splash ?
                <h1 className="title align-left">independant</h1>
             :   
                <span>
                <button onClick={this.props.buttonFunction}
                    className="btn btn-link btn-nav pull-left page_nav__prev">
                    <span className="icon icon-left-nav"></span> <span className="">Previous</span>
                </button>
                <h1 className="title">7 / 11</h1>
                </span>
            }

            <a className="icon icon-bars pull-right menu" onClick = {this.onClick} ></a>

            { this.state.showMenu ? <Menu /> : null }
            </header>
        )
    }

});

