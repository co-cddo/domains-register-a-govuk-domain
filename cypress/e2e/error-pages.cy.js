import './base.cy'

describe('Error pages (404/500 etc)', () => {
  it('shows a 404 govuk-styled page', () => {
    cy.visit("/doesnotexist-2432", { failOnStatusCode: false })
    cy.get('p').should('include.text', 'If you entered a web address, check it is correct.')
  })
})
