import './base.cy'

describe('change registrar organisation name', () => {
    it('goes back to the answers page after the user changed the registrar', () => {
      cy.goToConfirmation('')
      // Change registrar organisation name
      cy.get('a[href="/change-registrar"]').click()
      cy.get('#id_organisations_choice').clear().type('Fantastic Registrar')

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Fantastic Registrar')
    })

    it('does not go back to the answers page after the user changed the registrar but clicked Continue', () => {
      cy.goToConfirmation('')
      // Change registrar organisation name
      cy.get('a[href="/change-registrar"]').click()
      cy.get('#id_organisations_choice').clear().type('Fantastic Registrar')

      // Continue
      cy.get('#id_submit').click();
      cy.checkPageTitleIncludes('What is your email address')
    })


  })
