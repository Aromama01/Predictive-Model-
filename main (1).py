import streamlit as st
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


@st.cache_data
def load_ensemble_model():
    # Load the entire model from a file
    try:
        ensemble_model = joblib.load("ensemble_model_predictions.joblib")
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None
    return ensemble_model

def home_page():
    st.title("Loan Prediction App")
    st.write("Welcome to the Loan Prediction App. Use the menu to navigate.")

def loan_eligibility_page():
    st.title("Loan Eligibility Checker")
    st.write("Enter the required details to check your initial loan eligibility.")

    if 'initial_eligibility_result' not in st.session_state:
        st.session_state['initial_eligibility_result'] = None

    income = st.number_input("Monthly Income (£)")
    credit_score = st.number_input("Credit Score")

    if st.button("Check Initial Eligibility"):
        try:
            st.session_state['initial_eligibility_result'] = predict_loan_eligibility(income, credit_score)
        except Exception as e:
            st.error(f'Error in eligibility prediction: {e}')
            return

    if st.session_state['initial_eligibility_result']:
        st.write(f"Initial Loan Eligibility Result: {st.session_state['initial_eligibility_result']}")

        if st.session_state['initial_eligibility_result'] == "Eligible":
            show_additional_features()

@st.cache_data
def predict_loan_eligibility(income, credit_score):
    if income >= 50000 and credit_score >= 700:
        return "Eligible"
    else:
        return "Not Eligible"


def show_additional_features():
    """
    This function displays additional input fields for final loan eligibility confirmation.
    It handles user inputs, validates them, and predicts final eligibility based on these inputs.
    """

    st.title("Final Eligibility Confirmation")
    st.write("Please provide additional information for final eligibility confirmation.")

    # Input fields for additional features
    age = st.number_input("Age", min_value=20)  # Assuming age should be at least 20
    credit_amount = st.number_input("Amount of Loan (£)", min_value=0)  # Assuming credit amount should be non-negative

    # Dropdown for organization type
    organization_type_options = ['Business Entity Type 3', 'School', 'Government', 'Religion', 'Other', 'XNA',
                                  'Electricity', 'Business Entity Type 2', 'Self-employed',
                                  'Transport: type 2', 'Construction', 'Housing', 'Kindergarten',
                                  'Trade: type 7', 'Industry: type 11', 'Services', 'Transport: type 4',
                                  'Industry: type 1', 'Emergency', 'Medicine', 'Trade: type 2', 'University',
                                  'Police', 'Business Entity Type 1', 'Postal', 'Transport: type 3',
                                  'Industry: type 4', 'Agriculture', 'Restaurant', 'Culture', 'Hotel',
                                  'Industry: type 7', 'Industry: type 3', 'Bank', 'Military', 'Trade: type 3',
                                  'Industry: type 9']
    organization_type = st.selectbox("Select your Organization Type", organization_type_options)

    days_registration = st.number_input("Days Since Registration - How many days before the application did client change his registration	time only relative to the application?", min_value=365)
    days_id_publish = st.number_input("Days Since ID Publication - How many days before the application did client change the identity document with which he applied for the loan time only relative to the application?", min_value=180)

    # Dropdown for occupation type
    occupation_type_options = ['Laborers', 'Core staff', 'Accountants', 'Unknown', 'Drivers', 'Sales staff',
                                'Cleaning staff', 'Private service staff', 'Managers', 'Medicine staff',
                                'Cooking staff', 'High skill tech staff', 'Low-skill Laborers',
                                'Security staff', 'Realty agents', 'Secretaries', 'Waiters/barmen staff']
    occupation_type = st.selectbox("Select your Occupation Type", occupation_type_options)

    loan_annuity = st.number_input("Loan Annuity", min_value=0)

    if st.button("Confirm Final Eligibility"):
        # Input validation
        if not all([age, credit_amount, organization_type, days_registration, days_id_publish, occupation_type, loan_annuity]):
            st.warning('Please fill in all fields before confirming.')
            return

        # Prediction with error handling
        try:
            final_eligibility_result = predict_final_loan_eligibility(
                age, credit_amount, organization_type, days_registration, days_id_publish, occupation_type, loan_annuity
            )
            st.success(f"Final Loan Eligibility Result: {final_eligibility_result}")
        except Exception as e:
            st.error(f'Error in final eligibility prediction: {e}')
            logging.error(f'Prediction error: {e}')  # Logging the error


@st.cache_data
def predict_final_loan_eligibility(age, credit_amount, organization_type, days_registration, days_id_publish, occupation_type, loan_annuity):
    ensemble_model = joblib.load("ensemble_model_predictions.joblib")
    if 25 <= age <= 60 and credit_amount > 10000 and organization_type == 'Business Entity Type 3' and loan_annuity < 5000:
        final_eligibility_result = "Eligible"
    # This is a placeholder, you should replace it with your actual logic
    elif age > 30 and credit_amount < 50000 and organization_type == 'Business Entity Type 3':
        final_eligibility_result = "Eligible"
    elif (
            25 <= age <= 60
            and credit_amount > 10000
            and organization_type == 'Business Entity Type 3'
            and loan_annuity < 5000
            and days_registration < 365
            and days_id_publish < 180
            and occupation_type in ['Managers', 'High skill tech staff']
    ):
        final_eligibility_result = "Eligible"

    else:
        final_eligibility_result = "Not Eligible"

    return final_eligibility_result



if __name__ == "__main__":
    # Create a menu to navigate between Home page and Loan Eligibility
    menu = ["Home", "Loan Eligibility"]
    choice = st.sidebar.selectbox("Select Page", menu)

    # Display the selected page
    if choice == "Home":
        home_page()
    elif choice == "Loan Eligibility":
        loan_eligibility_page()

