describe('Change Answers', () => {
    it('verify changed answer', () => {
      cy.visit('http://0.0.0.0:8000/')

      // select org
      cy.get('select.govuk-select').select('34SP.com')
      cy.get('.govuk-button').click()

      // select email
      cy.get('.govuk-input').clear().type('a@b.com')
      cy.get('.govuk-button').click()

      // select registrar
      cy.get('#id_registrant_type_5').click()
      cy.get('.govuk-button').click()

      // check old value
      cy.get('.govuk-summary-list__value').should('include.text', 'a@b.com')

      // change email
      cy.get(':nth-child(3) > .govuk-summary-list__row > .govuk-summary-list__actions > .govuk-link').click();
      cy.get('#id_registrant_email_address').clear();
      // check changed email
      cy.get('#id_registrant_email_address').type('a1@b.com');
      cy.get('#id_cancel').click();
      
      // check new value
      cy.get('.govuk-summary-list__value').should('include.text', 'a1@b.com')
    })
})