import React from "react";
import { BrowserRouter, Route, Switch, HashRouter } from "react-router-dom";
import {
    Home,
    Login,
    Register,
    Upload,
    Article,
    Search,
    Profile,
    ProfileEdit
} from "pages";
import { Provider } from "react-redux";
import PropTypes from "prop-types";
import { PersistGate } from "redux-persist/integration/react";

const Root = ({ store, persistor }) => {
    return (
        <Provider store={store}>
            <PersistGate loading={null} persistor={persistor}>
                <HashRouter>
                    <BrowserRouter>
                        <Switch>
                            <Route exact path="/" component={Home} />
                            <Route exact path="/login/" component={Login} />
                            <Route
                                exact
                                path="/register/"
                                component={Register}
                            />
                            <Route exact path="/upload/" component={Upload} />
                            <Route
                                exact
                                path="/article/:id"
                                component={Article}
                            />
                            <Route exact path="/search/" component={Search} />
                            <Route
                                exact
                                path="/users/:user"
                                component={Profile}
                            />
                            <Route
                                exact
                                path="/profile/"
                                component={ProfileEdit}
                            />
                        </Switch>
                    </BrowserRouter>
                </HashRouter>
            </PersistGate>
        </Provider>
    );
};

Root.propTypes = {
    store: PropTypes.object.isRequired,
    persistor: PropTypes.object.isRequired
};

export default Root;
