# hinge-to-bearer

Reverse Engineered Hinge Authentication Flow 😍

A few months ago I worked on a project automated some hinge features. The client was really annoying to reverse engineer so I thought I would put the authentication flow code online so nobody else has to suffer.

The entire flow is contained in this file. Sadly, I have not yet included functionality for those who have created accounts with Apple / Google (I am actually not sure if reversing the Apple authentication flow is possible).

## Usage

Run `Auth.py`.

You will be prompted to enter your phone number. Please remember to include your country code in this.

Once you have entered your code it will initiate the email verification.

Once the email OTP is verified, you should be returned with your bearer token which you can do what you want with!
