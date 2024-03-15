import './base.cy'

describe('change domain name', () => {
    it('correctly changes the domain name when the users goes back to change it', () => {
      cy.base('')
      // Change domain name
      cy.visit("/domain/?change");
      cy.get('#id_domain_name').clear('');
      cy.get('#id_domain_name').type('Arrakis')

      // Back to Answers
      cy.get('#id_cancel').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Arrakis')
    })
  })
