# Use cases

To deomonstrate industrially relevant use of the MarketPlace plattform a total of six use cases were developed. These were:

1. **Laser powder bed fusion L-PBF** [Use case 1](./uc1.md).
1. **Screen printing of solid oxide fuel cells** [Use case 2](./uc2.md).
1. **Nano-particle production and catalyst testing** [Use case 3](./uc3.md).
1. **Ceramic injection moulding for medical applications** [Use case 4](./uc4.md).
1. **Printing of Photovoltaic Thin Films** [Use case 5](./uc5.md).
1. **MatCalc demo** [Use case 6](./uc6.md).

Implementation details for each use case can be found by clicking the individual links.
Below we give a more prosaic overview of each of the use cases.

   

All use cases, except the last, consist of at least two independent software programs where the output from one program forms part of the input to the second program. The software programs/tools used are all general purpose programs which can to some extent be customized and adopted further. Ideally, every relevant state or models would be syntactically described and accessible through an open API. However, this is rearly the case, and some cases may need bespoke customization to solve a particular problem. Thus, it would be a formiddable task to expose the entire user accessible/modifiable user interface. Instead the approach taken at this stage in the MarketPlace platform development is for experts to set up and configure these solvers for each solver in the use cases. For tested and validated use cases the end user is presented with a set of relevant parameters that can be changed by the user through a RestAPI. This is illustrated in schematic below: 
<br>
<img src="../\_static/img/ucs/uc_impl/RestAPI.png" width="350px"    >
<br>
<br>

<table>
  <tr> <th> Description </th> <th> Illustration </th> </tr>
  <tr>
    <td>
      <b style="font-size:30px">Use case 1: Laser powder bed fusion for additive manufacturing of super-alloys</b> <br>

```
  Executing patners: MTU, Fraunhofer, ACCESS, ANSYS-Granta, EPFL
```

</td>
<td>
      <img src="../\_static/img/ucs/uc_impl/uc1-01.png" width="350px"    >
      <br><br>
</td>
</tr>

<tr>
<td>
<b style="font-size:30px">Use case 2: Screen printing of solid oxide fuel cells</b> <br>

```
  Executing patners: Bosch, DCS, ANSYS-Granta
```
</td>
<td>
      <img src="../\_static/img/ucs/uc_impl/uc2-01.png" width="350px"    >  
</td>
</tr>
  
<tr>
<td>
<b style="font-size:30px">Use case 3: Nano-particle production and catalyst testing</b> <br>

```
  Executing patners: Johnson Matthey, Lurredera, SINTEF, ANSYS-Granta
```
</td>
<td>
      <img src="../\_static/img/ucs/uc_impl/uc3-01.png" width="350px"    >  
</td>
</tr>
  
<tr>
<td>
<b style="font-size:30px">Use case 4: Ceramic injection moulding for medical applications</b> <br>

```
  Executing patners: HES, DCS, ANSYS-Granta
```
</td>
<td>
      <img src="../\_static/img/ucs/uc_impl/uc4-01.png" width="350px"    >  
</td>
</tr>
  
<tr>
<td>
<b style="font-size:30px">Use case 5: Printing of Photovoltaic Thin Films</b> <br>

```
  Executing patners: Crystalsol, UCL
```
</td>
<td>
      <img src="../\_static/img/ucs/uc_impl/uc5-01.png" width="350px"    >  
</td>
</tr>

<tr>
<td>
<b style="font-size:30px">Use case 6: MatCalc demo</b> <br>

```
  Executing patners: MBN, Fraunhofer
```
</td>
<td>
      <img src="../\_static/img/ucs/uc_impl/uc6-01.png" width="350px"    >  
</td>
</tr>

</table>
