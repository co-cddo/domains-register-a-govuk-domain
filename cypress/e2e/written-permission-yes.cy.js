describe('Traverses to Written Permission page and selects Yes', () => {
    it('Traverses to Written Permission page and selects Yes', () => {
        cy.visit('http://0.0.0.0:8000/')

        cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
        cy.get('select.govuk-select').should('exist')

        cy.get('select.govuk-select').select('34SP.com')

        cy.get('.govuk-button#id_submit').click()

        cy.get('h1').should('include.text', 'What is your email address?')
        cy.get('.govuk-input').type('something@some.gov.uk')
        cy.get('.govuk-button#id_submit').click()

        cy.get('h1').should('include.text', 'Which of the following best describes your registrant\'s organisation?')
        cy.get('#id_registrant_type_2').click()
        cy.get('.govuk-button#id_submit').click()

        cy.get('h1').should('include.text', 'What is your registrant’s organisation name?')
        cy.get('.govuk-input').type('HMRC')
        cy.get('.govuk-button#id_submit').click()

        cy.get('h1').should('include.text', 'Does your registrant have written permission to apply for a .gov.uk domain name?')
        cy.get('#id_written_permission_1').click()
        cy.get('.govuk-button#id_submit').click()

        cy.get('h1').should('include.text', 'Upload evidence of written permission') // Should change later as more pages get added
    })
})
