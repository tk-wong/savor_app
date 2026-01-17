// File: __tests__/index_test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import Index from '../app/index';
import {Alert} from "react-native";

describe('Index screen', () => {
    const alertMock = jest.spyOn(Alert, 'alert');

    beforeEach(() => {
        jest.clearAllMocks();
    });

    afterAll(() => {
        alertMock.mockRestore();
    });

    it('renders username and password inputs and buttons', () => {
        const { getByPlaceholderText, getByText } = render(<Index/>);
        expect(getByPlaceholderText('User name')).toBeTruthy();
        expect(getByPlaceholderText('Password')).toBeTruthy();
        expect(getByText('Submit')).toBeTruthy();
        expect(getByText('Create account')).toBeTruthy();
    });

    it('alerts with name and password when Submit is pressed', () => {
        const { getByPlaceholderText, getByText } = render(<Index />);
        const usernameInput = getByPlaceholderText('User name');
        const passwordInput = getByPlaceholderText('Password');
        const submitBtn = getByText('Submit');

        fireEvent.changeText(usernameInput, 'alice');
        fireEvent.changeText(passwordInput, 'secret');
        fireEvent.press(submitBtn);

        expect(alertMock).toHaveBeenCalledWith("User information",'name: alice, password: secret');
    });

    it('alerts "Create account" when Create account is pressed', () => {
        const { getByText } = render(<Index />);
        const createBtn = getByText('Create account');

        fireEvent.press(createBtn);
        expect(alertMock).toHaveBeenCalledWith('Create account','Create account');
    });


});
