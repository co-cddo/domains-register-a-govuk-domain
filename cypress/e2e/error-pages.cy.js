import './base.cy'

describe('Error pages', () => {
  it('Shows a GOV.UK-themed 404 page', () => {
    cy.visit('/doesnotexist', { failOnStatusCode: false })
    cy.checkPageTitleIncludes('Page not found')
    cy.get('.govuk-body').should('include.text', 'If you entered a web address, check it is correct.')
  })

  it('Shows a GOV.UK-themed 301 page', () => {
    cy.start()
    cy.get('a.govuk-button--start').click()
    cy.checkPageTitleIncludes('Registrar details')
    cy.request({
      method: 'POST',
      url: '/registrar-details/',
      failOnStatusCode: false
    }).then( (res) => {
      expect(res.status).to.eq(403)
      expect(res.body).to.include('It looks like you\'ve tried to do something that\'s not allowed')
    })
  })
})
