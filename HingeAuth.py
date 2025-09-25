#!/usr/bin/env python3

import requests
import json
import uuid
import time
from typing import Dict, Any, Optional

class HingeAuthenticator:
    def __init__(self):

        self.base_url = "https://prod-api.hingeaws.net"
        self.session = requests.Session()
        
        # Generate session identifiers
        self.session_id = self._generate_uuid()
        self.device_id = self._generate_uuid()
        self.install_id = self._generate_uuid()
        
        print(f"Generated session identifiers:")
        print(f"Session ID: {self.session_id}")
        print(f"Device ID: {self.device_id}")
        print(f"Install ID: {self.install_id}")
    
    def _generate_uuid(self) -> str:
        """Generate a UUID in uppercase format"""
        return str(uuid.uuid4()).upper()
    
    def _get_base_headers(self) -> Dict[str, str]:
        """Get base headers for API requests"""
        return {
            'content-type': 'application/json',
            'x-device-platform': 'iOS',
            'user-agent': 'Hinge/11612 CFNetwork/3826.400.120 Darwin/24.3.0',
            'accept': '*/*',
            'x-session-id': self.session_id,
            'x-device-model-code': 'iPhone13,2',
            'x-install-id': self.install_id,
            'accept-language': 'en-GB',
            'accept-encoding': 'gzip, deflate, br',
            'x-build-number': '11614',
            'x-device-region': 'GB',
            'x-device-id': self.device_id,
            'x-app-version': '9.78.0',
            'x-device-model': 'iPhone 13',
            'x-os-version': '18.3.1'
        }
    
    def _init_auth(self) -> bool:
        """Initialize authentication by posting install ID"""
        print("Initializing authentication...")
        
        try:
            url = f"{self.base_url}/identity/install"
            headers = self._get_base_headers()
            payload = {"installId": self.install_id}
            
            print(f"Request URL: {url}")
            print(f"Request headers: {headers}")
            print(f"Request payload: {payload}")
            
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            print(f"Init auth status: {response.status_code}")
            print(f"Init auth response: {response.text}")
            
            return response.status_code in [200, 201, 204]
        
        except Exception as e:
            print(f"Error initializing auth: {e}")
            return False
    
    def initiate_sms(self, phone_number: str) -> bool:
        """
        Initiate SMS verification
        
        Args:
            phone_number: Phone number to send SMS to
            
        Returns:
            bool: True if SMS was initiated successfully
        """
        print(f"Initiating SMS for phone number: {phone_number}")
        
        # Initialize auth first
        if not self._init_auth():
            print("Failed to initialize authentication")
            return False
        
        try:
            url = f"{self.base_url}/auth/sms/v2/initiate"
            headers = self._get_base_headers()
            payload = {
                "phoneNumber": phone_number,
                "deviceId": self.device_id
            }
            
            print(f"SMS Request URL: {url}")
            print(f"SMS Request payload: {payload}")
            
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            print(f"SMS initiation status: {response.status_code}")
            print(f"SMS initiation response: {response.text}")
            
            if response.status_code in [200, 201, 204]:
                print("SMS initiated successfully")
                return True
            else:
                print(f"SMS initiation failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error initiating SMS: {e}")
            return False
    
    def validate_otp(self, phone_number: str, otp: str) -> Optional[Dict[str, Any]]:
        """
        Validate OTP code
        
        Args:
            phone_number: Phone number used for SMS
            otp: OTP code received via SMS
            
        Returns:
            dict: Response containing email and caseId if successful, None otherwise
        """
        print("Validating OTP...")
        
        try:
            url = f"{self.base_url}/auth/sms/v2"
            headers = self._get_base_headers()
            payload = {
                "phoneNumber": str(phone_number),
                "deviceId": self.device_id,
                "installId": self.install_id,
                "otp": str(otp)
            }
            
            print(f"OTP validation payload: {payload}")
            
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            print(f"OTP validation status: {response.status_code}")
            print(f"OTP validation response: {response.text}")
            
            try:
                response_data = response.json()
                print(f"Parsed OTP response: {response_data}")
                
                if response.status_code == 412 and 'caseId' in response_data:
                    return {
                        'email': response_data.get('email'),
                        'caseId': response_data.get('caseId')
                    }
                else:
                    print(f"OTP validation failed - status: {response.status_code}")
                    return None
                    
            except json.JSONDecodeError:
                print(f"Non-JSON response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error validating OTP: {e}")
            return None
    
    def validate_email_otp(self, case_id: str, email_code: str) -> Optional[str]:
        """
        Validate email OTP and get bearer token
        
        Args:
            case_id: Case ID from SMS validation
            email_code: OTP code received via email
            
        Returns:
            str: Bearer token if successful, None otherwise
        """
        print("Validating email OTP...")
        
        try:
            url = f"{self.base_url}/auth/device/validate"
            headers = self._get_base_headers()
            payload = {
                "caseId": case_id,
                "code": email_code,
                "deviceId": self.device_id,
                "installId": self.install_id
            }
            
            response = self.session.post(url, headers=headers, json=payload)
            print(f"Email OTP validation status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print("Email OTP validation successful!")
                
                bearer_token = response_data.get('token')
                if bearer_token:
                    print(f"Bearer token obtained: {bearer_token}")
                    return bearer_token
                else:
                    print("No token found in response")
                    return None
            else:
                print(f"Email OTP validation failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error validating email OTP: {e}")
            return None

def authenticate_hinge(phone_number: str) -> Optional[str]:
    """
    Complete authentication flow for Hinge
    
    Args:
        phone_number: Phone number to authenticate with
        
    Returns:
        str: Bearer token if successful, None otherwise
    """
    authenticator = HingeAuthenticator()

    if not authenticator.initiate_sms(phone_number):
        print("Failed to initiate SMS")
        return None

    sms_otp = input("Enter the SMS OTP code: ").strip()
    
    otp_result = authenticator.validate_otp(phone_number, sms_otp)
    if not otp_result:
        print("Failed to validate SMS OTP")
        return None
    
    print(f"Email: {otp_result['email']}")
    print(f"Case ID: {otp_result['caseId']}")
    
    email_otp = input("Enter the email OTP code: ").strip()
    
    bearer_token = authenticator.validate_email_otp(otp_result['caseId'], email_otp)
    
    return bearer_token

if __name__ == "__main__":

    phone_number = input("Enter your phone number: ").strip()
    
    token = authenticate_hinge(phone_number)
    
    if token:
        print(f"\n✅ Authentication successful!")
        print(f"Bearer Token: {token}")
    else:
        print("\n❌ Authentication failed!")