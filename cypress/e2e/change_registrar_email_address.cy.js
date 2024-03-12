import './base.cy'

describe('change Email address', () => {
    it('email address', () => {
      cy.base('')
      // Change Organisation name
      cy.get(':nth-child(6) > .govuk-summary-list__row > .govuk-summary-list__actions > .govuk-link').click();
      cy.get('#id_registrant_email_address').clear();
      cy.get('.govuk-input').type('something1@some.gov.uk')

      // Back to Answers
      cy.get('#id_cancel').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'something1@some.gov.uk')
    })
  })
  