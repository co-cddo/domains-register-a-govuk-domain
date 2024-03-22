import './base.cy'

describe('change domain name', () => {
    it('correctly changes the domain name when the users goes back to change it', () => {
      cy.goToConfirmation('')
      // Change domain name
      cy.get("a[href='/change-domain']").click()
      cy.get('#id_domain_name').clear('');
      cy.get('#id_domain_name').type('arrakis')

      // Back to Answers
      cy.get('#id_back_to_answers').click()
      cy.get('h1').should('include.text', 'Check your answers')
      cy.get('.govuk-summary-list__value').should('include.text', 'arrakis')

      // Pressing continue instead. Should move ahead to minister
      cy.get("a[href='/change-domain']").click()
      cy.get('#id_domain_name').clear('').type('harkonnen');
      cy.get('#id_submit').click();
      cy.get('h1').should('include.text', 'Has a central government minister')

    })
  })
