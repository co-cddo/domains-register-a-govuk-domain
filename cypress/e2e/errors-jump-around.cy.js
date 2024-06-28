import './base.cy'

describe('Errors when user skips and jumps pages', () => {
  it('Throws a 400 when user skips to success page', () => {

    cy.goToRegistrantDetails()

    cy.request({ url: '/success', failOnStatusCode: false}).then(res => {
      expect(res.status).to.eq(400)
      expect(res.body).to.include('Invalid request')
    })
  })
})
