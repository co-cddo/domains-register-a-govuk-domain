import './base.cy'

describe('Errors when uploading files', () => {
  it('Removes the exemption uploaded data', () => {

    cy.goToExemptionUploadConfirm('exemption.png')

    cy.get("#uploaded-filename").invoke('attr', 'href').then(uploadedFilename => {
      cy.get('#remove-link').click()
      cy.checkPageTitleIncludes('Upload evidence of the exemption')

      cy.get('input[type=file]').then(fileInputs => {
        expect(fileInputs.length).to.equal(1)
        expect(fileInputs[0].files.length).to.equal(0)
      })

      cy.request({
        url: '/' + uploadedFilename,
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404)
      })
    })
  })


  it('Removes the written permission uploaded data', () => {
    cy.goToWrittenPermissionUploadConfirm('permission.png')

    cy.get("#uploaded-filename").invoke('attr', 'href').then(uploadedFilename => {
      cy.get('#remove-link').click()
      cy.checkPageTitleIncludes('Upload evidence of permission')

      cy.get('input[type=file]').then(fileInputs => {
        expect(fileInputs.length).to.equal(1)
        expect(fileInputs[0].files.length).to.equal(0)
      })

      cy.request({
        url: '/' + uploadedFilename,
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404)
      })
    })
  })


  it('Removes the minister uploaded data', () => {
    cy.goToMinisterUploadConfirm('minister.png')

    cy.get("#uploaded-filename").invoke('attr', 'href').then(uploadedFilename => {
      cy.get('#remove-link').click()
      cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')

      cy.get('input[type=file]').then(fileInputs => {
        expect(fileInputs.length).to.equal(1)
        expect(fileInputs[0].files.length).to.equal(0)
      })

      cy.request({
        url: '/' + uploadedFilename,
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404)
      })
    })
  })
})
