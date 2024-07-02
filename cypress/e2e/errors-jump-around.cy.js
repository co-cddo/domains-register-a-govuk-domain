import './base.cy'

describe('Errors when user skips and jumps pages', () => {
  it('Throws a 404 when user skips to success page', () => {

    cy.goToRegistrantDetails()

    cy.request({ url: '/success', failOnStatusCode: false}).then(res => {
      expect(res.status).to.eq(404)
    })
  })

  it('Throws a 200 when user skips to success page with param', () => {

    cy.goToRegistrantDetails()

    cy.request({ url: '/success/abc', failOnStatusCode: false}).then(res => {
      expect(res.status).to.eq(200)
      expect(res.body).to.include('abc')
    })
  })
})
