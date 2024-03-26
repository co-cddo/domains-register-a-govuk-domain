import './base.cy'

describe('change Email address', () => {
    it('correctly changes the email address when the users goes back to change it', () => {
      cy.goToConfirmation('')
      // Change email
      cy.get('a[href="/change-email"]').click()

      // check that existing value is pre-populated
      cy.get('#id_registrar_email_address').should('have.value', 'weregister@example.com')

      // Change the value
      cy.get('#id_registrar_email_address').clear()
      cy.get('#id_registrar_email_address').type('weregister2@example.com')

      // click "Back to Answers"
      cy.get('#id_back_to_answers').click()
      cy.checkPageTitleIncludes('Check your answers')
      cy.get('.govuk-summary-list__value').should('include.text', 'weregister2@example.com')

      // Change email again
      cy.get('a[href="/change-email"]').click()
      cy.get('#id_registrar_email_address').clear()
      cy.get('#id_registrar_email_address').type('weregister3@example.com')

      // Click submit, so should not go back to answers but instead continue the flow
      cy.get('#id_submit').click()
      cy.checkPageTitleIncludes('Which of the following')
    })
  })
