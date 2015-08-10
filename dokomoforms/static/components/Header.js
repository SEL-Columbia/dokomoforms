var React = require('react');
var Menu = require('./baseComponents/Menu.js');

/*
 * Header component
 * Displays the top bar of the Application, includes hambaagah menu
 *
 * props:
 *  @splash: Boolean to render splash header instead of the default
 *  @buttonFunction: What to do on previous button click
 *  @number: Current number to render in header
 *  @db: Active pouch db // XXX rather not pass this to header
 */
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
                <h1 className="title">{this.props.number} / {this.props.total}</h1>
                </span>
            }

            <a className="icon icon-bars pull-right menu" onClick = {this.onClick} ></a>

            { this.state.showMenu ? <Menu db={this.props.db}/> : null }
            </header>
        )
    }

});

