import './base.cy'

describe('Email format verification', () => {
  it('Should give an error if the text entered isn\'t a valid email', () => {

    cy.goToRegistrarEmail()

    // although email addresses are checked by the browser, we can't expect all
    // browsers to do so, so we do need to check server-side
    cy.get('.govuk-input').type('a@b.c') // Somehow Chrome allows this one
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('What is your email address?')
    cy.get('#error-summary-title').should('include.text', 'There is a problem')
    cy.get('#id_registrar_email_address_1_error').should('include.text', 'Please enter a valid email address')

    cy.get('.govuk-input').clear().type('a@b.com')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Which of the following best describes your registrant\'s organisation?')

  })
})
