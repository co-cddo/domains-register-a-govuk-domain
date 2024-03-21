import './base.cy'

describe('change Email address', () => {
    it('correctly changes the email address when the users goes back to change it', () => {
      cy.goToConfirmation('')
      // Change email
      cy.get('a[href="/change-email"]').click()
      cy.get('#id_registrant_email_address').clear()
      cy.get('#id_registrant_email_address').type('something1@some.gov.uk')

      // click "Back to Answers"
      cy.get('#id_back_to_answers').click()
      cy.get('h1').should('include.text', 'Check your answers')
      cy.get('.govuk-summary-list__value').should('include.text', 'something1@some.gov.uk')

      // Change email again
      cy.get('a[href="/change-email"]').click()
      cy.get('#id_registrant_email_address').clear()
      cy.get('#id_registrant_email_address').type('something2@some.gov.uk')

      // Click submit, so should not go back to answers but instead continue the flow
      cy.get('#id_submit').click()
      cy.get('h1').should('include.text', 'Which of the following')
    })


  })
