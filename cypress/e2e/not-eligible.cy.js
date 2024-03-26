describe('Registrant not eligible', () => {
  it('Says registrant is not eligible if user selects other type of organisation', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('#id_organisations_choice').type('WeRegister')
    cy.get('.govuk-button#id_submit').click()


    cy.checkPageTitleIncludes('What is your email address?')
    cy.get('.govuk-input').type('something@some.gov.uk')
    cy.get('.govuk-button#id_submit').click()


    cy.checkPageTitleIncludes('Which of the following best describes your registrant\'s organisation?')
    cy.get('#id_registrant_type_12').click()
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Your registrant is not eligible for a .gov.uk domain name')

  })
})
