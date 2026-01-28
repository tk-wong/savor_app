// File: __tests__/index_test.tsx
import React from 'react';
import { render, fireEvent ,screen} from '@testing-library/react-native';
import LoginPage from '../app/loginPage';
import {Alert, Platform} from "react-native";
import {renderRouter} from "expo-router/testing-library";

import {router} from "expo-router";


describe('Index screen', () => {
    const alertMock = jest.spyOn(Alert, 'alert');
    const navigateMock = jest.spyOn(router,'navigate')

    beforeEach(() => {
        jest.clearAllMocks();
    });

    afterAll(() => {
        alertMock.mockRestore();
    });

    it('renders username and password inputs and buttons', () => {
        render(<LoginPage/>);
        expect(screen.getByPlaceholderText('User name')).toBeTruthy();
        expect(screen.getByPlaceholderText('Password')).toBeTruthy();
        expect(screen.getByText('Submit')).toBeTruthy();
        expect(screen.getByText('Create account')).toBeTruthy();
    });

    it('alerts with name and password when Submit is pressed', () => {
        const { getByPlaceholderText, getByText } = render(<LoginPage />);
        const usernameInput = getByPlaceholderText('User name');
        const passwordInput = getByPlaceholderText('Password');
        const submitBtn = getByText('Submit');

        fireEvent.changeText(usernameInput, 'alice');
        fireEvent.changeText(passwordInput, 'secret');
        fireEvent.press(submitBtn);

        expect(alertMock).toHaveBeenCalledWith("User information",'name: alice, password: secret');
    });

    it('alerts "Create account" when Create account is pressed', () => {
        renderRouter(

        )
        const { getByText } = render(<LoginPage />);
        const createBtn = getByText('Create account');

        fireEvent.press(createBtn);
        expect(navigateMock).toHaveBeenCalledWith('/createUserPage');
    });


});
