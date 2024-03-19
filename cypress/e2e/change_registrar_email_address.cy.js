import './base.cy'

describe('change Email address', () => {
    it('correctly changes the email address when the users goes back to change it', () => {
      cy.base('')
      // Change email
      cy.visit("email/?change")
      cy.get('#id_registrant_email_address').clear();
      cy.get('#id_registrant_email_address').type('something1@some.gov.uk')

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'something1@some.gov.uk')
    })
  })
