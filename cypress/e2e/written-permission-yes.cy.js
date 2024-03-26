describe('Traverses to Written Permission page and selects Yes', () => {
    it('Traverses to Written Permission page and selects Yes', () => {
        cy.visit('http://0.0.0.0:8000/')

        cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
        cy.get('select.govuk-select').should('exist')

        cy.get('#id_organisations_choice').type('WeRegister')

        cy.get('.govuk-button#id_submit').click()

        cy.checkPageTitleIncludes('What is your email address?')
        cy.get('.govuk-input').type('something@some.gov.uk')
        cy.get('.govuk-button#id_submit').click()

        cy.checkPageTitleIncludes('Which of the following best describes your registrant\'s organisation?')
        cy.get('#id_registrant_type_3').click()
        cy.get('.govuk-button#id_submit').click()

        cy.checkPageTitleIncludes('What is your registrant’s organisation name?')
        cy.get('.govuk-input').type('HMRC')
        cy.get('.govuk-button#id_submit').click()

        cy.checkPageTitleIncludes('Does your registrant have written permission to apply for a .gov.uk domain name?')
        cy.get('#id_written_permission_1').click()
        cy.get('.govuk-button#id_submit').click()

        cy.checkPageTitleIncludes('Upload evidence of written permission') // Should change later as more pages get added
    })
})
